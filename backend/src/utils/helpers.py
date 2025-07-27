# Common helper functions


from datetime import datetime
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