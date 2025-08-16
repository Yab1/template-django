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
            # Handle DRF validation errors with our custom format
            if "message" in data:
                return data["message"]
                # Don't stringify the extra data, let it remain as object

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
            # For error responses, preserve the structure from exception handler
            if isinstance(data, dict) and "message" in data and "extra" in data:
                # Data is already formatted by our exception handler
                formatted_data = {
                    "status": "error",
                    "result": None,
                    "meta": {
                        "version": "v1",
                        **additional_meta,
                    },
                    "message": data["message"],
                    "extra": data["extra"],  # Preserve the extra structure
                }
            else:
                # Fallback for other error formats
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
