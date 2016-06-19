class Attachment:
    """
    Encapsulates an abstraction of an email attachment that's useful
    for processing and storage
    """
    def __init__(self, content, content_type, filename=None):
        """
        Initializer for the Attachment class
        :return: None
        """
        self.filename = filename
        self.content_type = content_type
        self.base64_content = content

    def to_dict(self):
        """
        Returns a dict representation of the attachment
        :return: dict
        """
        return {
            'filename': self.filename,
            'content_type': self.content_type,
            'content': self.base64_content
        }
