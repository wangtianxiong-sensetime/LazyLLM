from typing import List, Optional, Dict
from lazyllm import LOG

from .doc_node import DocNode, ImageDocNode
from .store import LAZY_ROOT_NAME, LAZY_IMAGE_GROUP
from .dataReader import SimpleDirectoryReader

class DirectoryReader:
    def __init__(self, input_files: Optional[List[str]], local_readers: Optional[Dict] = None,
                 global_readers: Optional[Dict] = None) -> None:
        self._input_files = input_files
        self._local_readers = local_readers
        self._global_readers = global_readers

    def load_data(self, input_files: Optional[List[str]] = None, metadatas: Optional[Dict] = None,
                  *, split_image_nodes: bool = False) -> List[DocNode]:
        input_files = input_files or self._input_files
        file_readers = self._local_readers.copy()
        for key, func in self._global_readers.items():
            if key not in file_readers: file_readers[key] = func
        LOG.info(f"DirectoryReader loads data, input files: {input_files}")
        reader = SimpleDirectoryReader(input_files=input_files, file_extractor=file_readers, metadatas=metadatas)
        nodes: List[DocNode] = []
        image_nodes: List[ImageDocNode] = []
        for doc in reader():
            doc._group = LAZY_IMAGE_GROUP if isinstance(doc, ImageDocNode) else LAZY_ROOT_NAME
            if not split_image_nodes or not isinstance(doc, ImageDocNode):
                nodes.append(doc)
            else:
                image_nodes.append(doc)
        if not nodes and not image_nodes:
            LOG.warning(
                f"No nodes load from path {input_files}, please check your data path."
            )
        LOG.info("DirectoryReader loads data done!")
        return (nodes, image_nodes) if split_image_nodes else nodes
