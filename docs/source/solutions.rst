===============================
Solutions and project structure
===============================

Dependencies
------------

| **Mongo DB** - used to store meta-information about documents and specifications.
| **Minio** - used to store files and version them.

Implementation features
-----------------------
* The microservice, in addition to storing meta-information according to the TMF specification, can save a file and add
  information about it to the document description. Able to request a temporary link to a file and redirect the user to
  this link
* The filtering method is implemented in more detail than in this specification, but may cause unforeseen errors.

Objects
-------

Document
^^^^^^^^
.. automodule:: schemas.document
   :members:

Document Specification
^^^^^^^^^^^^^^^^^^^^^^
.. automodule:: schemas.document_specification
   :members:
