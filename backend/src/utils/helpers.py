# Common helper functions


from datetime import date, datetime
import numpy as np
import pandas as pd


def convert_date_to_datetime(date) -> datetime:
        """Convert pandas index date to datetime object"""
        try:
            # Try pandas Timestamp conversion first
            return pd.Timestamp(date).to_pydatetime()
        except:
            try:
                # Try direct datetime conversion
                return datetime.fromisoformat(str(date).split()[0])
            except:
                # Last resort - parse string manually
                date_str = str(date).split()[0]  # Get just the date part
                return datetime.strptime(date_str, '%Y-%m-%d')
            


def make_json_serializable(obj):
    """Convert any object to JSON-serializable format"""
    try:
        if isinstance(obj, dict):
            # Handle dictionaries - ensure all keys are strings
            result = {}
            for key, value in obj.items():
                # Convert key to string to avoid unhashable type errors
                str_key = str(key)
                # Recursively serialize the value
                result[str_key] = make_json_serializable(value)
            return result
        elif isinstance(obj, (list, tuple)):
            return [make_json_serializable(item) for item in obj]
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, pd.Series):
            return obj.tolist()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict('records')
        elif isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        elif pd.isna(obj):
            return None
        elif obj is None:
            return None
        elif isinstance(obj, (str, int, float, bool)):
            return obj
        else:
            # For any other type, convert to string as fallback
            return str(obj)
    except Exception as e:
        print(f"Error serializing {type(obj)}: {e}")
        return str(obj)