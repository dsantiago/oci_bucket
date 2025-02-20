# OCI Bucket Framework 

For easier OCI blob manipulation, read, download, etc.

## Import
```python
from oci_bucket import OciBucket
```

## Load from Instance Principal
```python
storage_client = OciBucket.client().from_instance_principal()
oci_bucket = OciBucket(storage_client, bucket_name)
```

## Load from OCI Config File 
```python
storage_client = OciBucket.client().from_file() # Defaults to ~/.oci/config
oci_bucket = OciBucket(storage_client, bucket_name)
```

## Methods 
Note that `limit` is set to 1000 by default, this limitation comes from original `oci.object_storage.ObjectStorageClient.object_list`.
This lib can go further and handle the pagination for you, just use `limit` beyond 1000.

```python
files = oci_bucket.list_folder('multiples', limit=12) # retrives files from directory
files = oci_bucket.glob('multiples/1{1,2}0{3,4}.txt', limit=2000) # Linux ls pattern can be used for blob filtering.
file = oci_bucket.get_file('multiples/0005.txt') # Or just retrieve files direct
```

## Blob Usage
As you can retrieve both a list of files or just a specific one, the blob files have methods on their own.

### Load Pandas dataframe Direct From CSV file bytes.
```python
import pandas as pd
from io import BytesIO
file_bytes = oci_bucket.get_file('csvs/acdc.csv').get_bytes()
df = pd.read_csv(BytesIO(file_bytes))
```
### Or just get the file and download it locally.
```python
oci_bucket.get_file('csvs/acdc.csv').download('acdc_new.csv')
```
