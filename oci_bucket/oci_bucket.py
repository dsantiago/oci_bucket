from oci.object_storage import ObjectStorageClient
import re


class OciClient:
    #-------------------------------
    @staticmethod
    def from_file(path='~/.oci/config'):
        import oci
        config = oci.config.from_file(path) 
        return ObjectStorageClient(config)

    #-------------------------------
    @staticmethod
    def from_instance_principal():
        from oci.auth import signers
        signer = signers.InstancePrincipalsSecurityTokenSigner()
        return ObjectStorageClient(config={}, signer=signer)


class OciBucket:

    #-------------------------------
    @staticmethod
    def client():
        return OciClient
    
    #-------------------------------        
    def __init__(self, client, bucket_name):
        self.client = client
        self.ns = client.get_namespace().data
        self.bucket_name = bucket_name
        self.blob_cache = None

    #-------------------------------
    def list_folder(self, folder, limit=1000):
        next_start = None
        lim = limit
        all_objs = []
        
        while True:
            response = self.client.list_objects(
                self.ns, 
                self.bucket_name, 
                prefix=folder, 
                limit=min(lim, 1000),
                fields='size,timeModified',
                start=next_start
            )

            lim -= min(lim, 1000)
            all_objs += response.data.objects
        
            if len(all_objs) >= limit or not (next_start := response.data.next_start_with):
                break
        
        return [OciBlob(obj, client=self.client, bucket_name=self.bucket_name) for obj in all_objs]

    #-------------------------------
    def glob(self, pattern, limit=1000):
        prefix = pattern

        if prefix[0] == '*':
            prefix = None
        elif '*' in prefix:
            prefix = prefix.split('*')[0]
        elif '{' in prefix:
            prefix = prefix[:prefix.index('{')]

        blobs = self.list_folder(prefix, limit=limit)
        # return blobs

        pattern = re.sub(r"\{([^}]+)\}", r"(\1)", pattern)
        pattern = pattern.replace('.', '\\.').replace('*', '.*').replace(',', '|')
        pattern = re.compile(f"^{pattern}$")
        pattern = re.compile(pattern)

        blobs = [b for b in blobs if pattern.match(b.filepath)]
        #     blobs = [b for b in blobs if b.filepath.endswith(suffix)]
                     
        return blobs

    #-------------------------------
    def get_file(self, filepath):
        if self.blob_cache is not None and self.blob_cache.filepath == filepath:
            return self.blob_cache
            
        response = self.client.list_objects(
            self.ns, 
            self.bucket_name, 
            prefix=filepath, 
            fields='size,timeModified', 
            limit=1
        )

        if response.status != 200:
            raise FileNotFoundError(f'File "{filepath}" not found.')

        obj = response.data.objects[0]
        self.blob_cache = OciBlob(obj, client=self.client, bucket_name=self.bucket_name) 
        return self.blob_cache


class OciBlob:
    #-------------------------------
    def __init__(self, obj, client, bucket_name):
        self.client = client
        self.ns = client.get_namespace().data
        self.bucket_name = bucket_name
        self.filepath = obj.name
        self.size = obj.size
        self.time_modified = obj.time_modified
    #-------------------------------
    def __repr__(self):
        params = dict(filepath=self.filepath, size=self.size)
        params = ", ".join(f"{k}={v}" for k, v in params.items())
        return f"{self.__class__.__name__}({params})"
    #-------------------------------
    def get_bytes(self):
        blob = self.client.get_object(self.ns, self.bucket_name, self.filepath)
        return blob.data.content #.decode("utf-8")
    #-------------------------------
    def download(self, filepath):
        with open(filepath, "wb") as f:
            f.write(self.get_bytes())
        
        
    
