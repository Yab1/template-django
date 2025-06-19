import json

from rest_framework.renderers import JSONRenderer


class CustomJSONRenderer(JSONRenderer):
    def _format_error_message(self, data):
        """Helper method to format error messages in a consistent way."""
        if isinstance(data, str):
            try:
                # Try to parse if it's a JSON string
                data = json.loads(data)
            except json.JSONDecodeError:
                return data

        if isinstance(data, dict):
            # Handle DRF validation errors
            if "message" in data:
                error_message = data["message"]
                if "extra" in data and isinstance(data["extra"], dict):
                    if "fields" in data["extra"]:
                        field_errors = data["extra"]["fields"]
                        if isinstance(field_errors, list):
                            field_errors = [str(err) for err in field_errors]
                            return f"{error_message}: {"; ".join(field_errors)}"  # Fixed line
                return error_message

            # Handle other dictionary error formats
            error_parts = []
            for key, value in data.items():
                if isinstance(value, (list, dict)):
                    error_parts.append(f"{key}: {json.dumps(value)}")
                else:
                    error_parts.append(f"{key}: {str(value)}")
            return "; ".join(error_parts)

        return str(data)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response", None)

        # Check if the data is already formatted with our structure
        if isinstance(data, dict) and all(key in data for key in ["result", "meta", "message"]):
            # If it's already formatted, just add version to meta if not present
            if "version" not in data["meta"]:
                data["meta"]["version"] = "v1"
            return super().render(data, accepted_media_type, renderer_context)

        # Get any additional metadata from the response data
        additional_meta = {}
        if isinstance(data, dict):
            if "meta" in data:
                additional_meta = data.pop("meta")
            # Extract result if it exists in data
            result_data = data.pop("result", data)
        else:
            result_data = data

        if response and response.status_code >= 400:
            formatted_data = {
                "status": "error",
                "result": None,
                "meta": {
                    "version": "v1",
                    **additional_meta,
                },
                "message": self._format_error_message(data),
            }
        else:
            formatted_data = {
                "status": "success",
                "result": result_data,
                "meta": {
                    "version": "v1",
                    **additional_meta,
                },
                "message": "Request processed successfully",
            }

        return super().render(formatted_data, accepted_media_type, renderer_context)
