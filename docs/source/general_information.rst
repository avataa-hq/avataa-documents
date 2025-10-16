General information
===================
This microservice is developed based on the `TMF 667 standard (version 4) <https://www.tmforum.org/resources/how-to-guide/tmf667-document-api-user-guide-v4-0-0/>`_

TMF667 Document API describes the meta-data of a Document,
such as the name, creationDate and lifecycle status.
The (typically binary) body of this document
(such as a Word.doc, PDF, Video clip, or Image)
will be held in the associated Attachment(s) either by Ref
or Value. If by value - the binary content is held in
the Attachment.content. If by reference,
the Attachment.url might point to a (file:)
or remote (http:) pointer to the Document media.
A Document may be associated with a DocumentSpecification,
which will detail the characteristics of that type of
Document (an Image may have a width, height and format;
a Video may have a length and format).
A Document has a collection of RelatedParty's,
for roles such as author, reviewer, publisher,
and a lifecycle status to take the document through a
simple set of production stages.