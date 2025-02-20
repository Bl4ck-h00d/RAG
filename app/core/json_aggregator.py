from typing import Dict, Any, Optional, List
from enum import Enum
import json
from weaviate.classes.query import Filter
from collections import Counter
from statistics import mean, median


class AggregationOperationType(Enum):
    COUNT = "count"
    SUM = "sum"
    MEAN = "mean"
    MODE = "mode"
    MEDIAN = "median"
    MIN = "min"
    MAX = "max"
    TEXT_OCCURRENCES = "text_occurrences"


class JSONAggregator:
    def __init__(self, store_client, embedding_generator):
        self.store_client = store_client
        self.collection = self.store_client.collections.get("Document")
        self.embedding_generator = embedding_generator

    def _get_nested_value(self, obj: Dict, path: str) -> List[Any]:
        """
        Define notation to access nested values in the object

        Supports:
        - Simple paths: 'json.field1'
        - Array access: 'json.field1[].field2'
        - Nested arrays: 'json.field1[].field2[].field3'
        - Nested objects: 'json.field1.field2.field3'
        - Nested object in arrays: 'json.field1.field2[].field3[].field4.field5
        """
       
        try:
            # Parse JSON string
            if isinstance(obj.get('json'), str):
                json_data = json.loads(obj.get('json'))
            else:
                json_data = obj.get('json')

            # Clean up field_path
            sub_paths = path.split('.')

            # discard 'json' prefix
            if sub_paths[0] == 'json':
                sub_paths = sub_paths[1:]

            # Traverse the JSON object
            return self._extract_values(json_data, sub_paths)
        except Exception as e:
            print(f"Error extracting values: {e}")
            return []

    def _extract_values(self,data_obj_context: Any, paths: List[str]) -> List[Any]:
        if not paths:
            return [data_obj_context] if data_obj_context is not None else []

        path = paths[0]
        remaining_paths = paths[1:]

        # Handle array notation
        if path.endswith('[]'):
            field_name=path[:-2]
            if isinstance(data_obj_context,dict):
                data_obj_context=data_obj_context.get(field_name)
            if isinstance(data_obj_context,list):
                results=[]
                for item in data_obj_context:
                    results.extend(self._extract_values(
                        item,remaining_paths
                    ))
                return results
            return []
        
        # Handle object notation
        if isinstance(data_obj_context, dict):
            return self._extract_values(
                data_obj_context.get(path),
                remaining_paths
            )
        elif isinstance(data_obj_context,list):
            results=[]
            for item in data_obj_context:
                if isinstance(item,dict):
                    results.extend(self._extract_values(item.get(path),remaining_paths))
            return results
        return []
    
    def _aggregate_values(self, values: List[Any], operation: AggregationOperationType, min_occurrences: int = 1) -> Any:
        """Perform aggregation operation on a list of values"""
        if not values:
            return None
        
        # Convert any dictionary values to strings for counting
        processed_values = []
        for value in values:
            if isinstance(value, dict):
                # Convert dict to a string representation or extract specific field
                processed_values.append(str(value))
            else:
                processed_values.append(value)

        if operation == AggregationOperationType.COUNT:
            return len(processed_values)

        elif operation == AggregationOperationType.TEXT_OCCURRENCES:
            # Ensure all values are strings for counting
            str_values = [str(v) for v in processed_values]
            counter = Counter(str_values)
            occurrences = [
                {"value": value, "count": count}
                for value, count in counter.items()
                if count >= min_occurrences
            ]
            return sorted(occurrences, key=lambda x: (-x["count"], x["value"]))

        # Numeric operations
        try:
            numeric_values = [float(v) for v in processed_values if str(
                v).replace('.', '').isdigit()]
            if not numeric_values:
                return None

            if operation == AggregationOperationType.SUM:
                return sum(numeric_values)
            elif operation == AggregationOperationType.MEAN:
                return mean(numeric_values)
            elif operation == AggregationOperationType.MEDIAN:
                return median(numeric_values)
            elif operation == AggregationOperationType.MIN:
                return min(numeric_values)
            elif operation == AggregationOperationType.MAX:
                return max(numeric_values)
            elif operation == AggregationOperationType.MODE:
                return Counter(numeric_values).most_common(1)[0][0]
        except (ValueError, TypeError):
            return None


    def aggregate(
            self,field_path:str,
            operation: AggregationOperationType,
            doc_id:str=None,
            min_occurrences:int=1,
            distance:Optional[float]=None,
            query_text:Optional[str]=None
    )->Dict[str,any]:
    
        """
        Perform custom aggregation on JSON fields
        """
        try:
            # Build the query
            query=self.collection.query

            # Filter if doc_id is provided
            filters=None
            if doc_id:
                filters=Filter.by_property("doc_id").equal(doc_id)

            # Add vector search if query_text is provided
            if query_text and self.embedding_generator:
                query_vector=self.embedding_generator.generate(query_text)

                if distance:
                    response=query.near_vector(
                        near_vector=query_vector,
                        distance=distance,
                        filters=filters
                    ).do()
                else:
                    # Use hybrid search if no distance specified
                    response=query.hybrid(
                        query=query_text,
                        vector=query_vector,
                        alpha=0.5,
                        filters=filters
                    ).do()
            
            else:
                # Use basic query with filters
                if filters:
                    response = query.fetch_objects(filters=filters)
                else:
                    response = query.fetch_objects()

                # Extract and aggregate values
                all_values = []
                for obj in response.objects:
                    values = self._get_nested_value(obj.properties, field_path)
                    all_values.extend(values)
                # Perform aggregation
                result = self._aggregate_values(
                    all_values, operation, min_occurrences)

                # Format response
                response_data = {
                    "field": field_path,
                    "operation": operation.value,
                }
                

                if operation == AggregationOperationType.TEXT_OCCURRENCES:
                    response_data["occurrences"] = result
                else:
                    response_data["value"] = result

                return response_data
        except Exception as e:
            print(f"Aggregation error: {str(e)}")
            raise