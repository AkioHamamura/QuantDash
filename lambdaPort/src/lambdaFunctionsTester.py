import unittest
import pandas as pd
from http.client import responses
from lambdaPort.src.utils.globals import BUCKET_NAME, DATA_PATH
from lambdaPort.src.utils.s3crud import (
    list_s3_objects_client,
    put_s3_objects_client,
    read_s3_object_client
)
from lambdaPort.src.data.data_fetcher import (write_available_tickers, fetch_cached_data, fetch_stock_data)

class S3OperationsTest(unittest.TestCase):
    """Test suite for S3 bucket operations"""

    def setUp(self):
        """Set up test data"""
        self.test_data = pd.DataFrame({
            'col1': [1, 2],
            'col2': [3, 4]
        })
        self.test_object_key = 'test.csv'
        self.read_object_key = 'cache/AAPL_max_None_None_1d_data.parquet'
        #self.read_object_key = 'test.csv'
    def test_list_bucket_objects(self):
        """Test listing objects in S3 bucket"""
        result = list_s3_objects_client(BUCKET_NAME)
        self.assertIn(result['statusCode'], [200, 201],
                     "Failed to list bucket objects")

    def test_upload_object(self):
        """Test uploading object to S3 bucket"""
        result = put_s3_objects_client(
            bucket_name=BUCKET_NAME,
            data=self.test_data,
            object_key=self.test_object_key
        )
        self.assertIn(result['statusCode'], [200, 201],
                     "Failed to upload object to bucket")

    def test_read_object(self):
        """Test reading object from S3 bucket"""
        result = read_s3_object_client(
            bucket_name=BUCKET_NAME,
            object_key=self.read_object_key
        )
        self.assertIn(result['statusCode'], [200, 201],
                     "Failed to read object from bucket")

class DataFetcherTest(unittest.TestCase):
    """Test suite for data fetcher functionality"""

    def test_write_available_tickers(self):
        """Test writing available tickers"""
        try:
            write_available_tickers(cache_dir=DATA_PATH)
            self.assertTrue(True)  # If we reach here, no exception was raised
        except Exception as e:
            self.fail(f"write_available_tickers raised an exception: {str(e)}")

    def test_fetch_cached_date(self):
        try:
            result = fetch_cached_data(ticker="NVDA", period="max", interval="1d")
            self.assertIsInstance(result, pd.DataFrame, "fetch_cached_data did not return a DataFrame")
            self.assertGreater(result.shape[0], 0, "fetch_cached_data returned an empty DataFrame")
        except Exception as e:
            self.fail(f"fetch_cached_data raised an exception: {str(e)}")

    def test_fetch_stock_data(self):
        try:
            result = fetch_stock_data(ticker="PLTR", period="max", interval="1d")
            self.assertIsInstance(result, pd.DataFrame, "fetch_stock_data did not return a DataFrame")
            self.assertGreater(result.shape[0], 0, "fetch_stock_data returned an empty DataFrame")
        except Exception as e:
            self.fail(f"fetch_stock_data raised an exception: {str(e)}")

def run_tests():
    """Run all test suites"""
    test_suites = [
        unittest.TestLoader().loadTestsFromTestCase(S3OperationsTest),
        unittest.TestLoader().loadTestsFromTestCase(DataFetcherTest)
    ]
    
    combined_suite = unittest.TestSuite(test_suites)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(combined_suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit_code = 0 if success else 1
    exit(exit_code)