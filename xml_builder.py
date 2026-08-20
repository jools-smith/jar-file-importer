from dataclasses import dataclass, field


@dataclass
class XMLBuilder:
    namespace = "urn:com.macrovision:flexnet/operations/exportimport"
    encoding = "UTF-8"
    version = "1.0"

    buffer: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)

    def new_line(self):
        self.buffer.append("\n")

    def initialize(self, tag):
        self.buffer.append(f'<?xml version="{XMLBuilder.version}" encoding="{XMLBuilder.encoding}"?>')
        self.new_line()
        self.new_line()
        self.buffer.append(f'<{tag} xmlns="{XMLBuilder.namespace}">')
        self.new_line()
        self.push_tag(tag, False)

    def push_tags(self, *tags):
        for tag in tags:
            self.push_tag(tag)

    def push_tag(self, tag, print=True):
        self.tags.append(tag)
        if print:
            self.buffer.append(f'<{tag}>')
            self.new_line()

    def pop_tag(self, target):
        while True:
            tag = self.tags.pop()
            self.buffer.append(f'</{tag}>')
            self.new_line()
            if tag == target:
                break

    def push_cdata(self, tag, value):
        self.push_value(tag, f'<![CDATA[{value}]]>')

    def push_value(self, tag, value):
        self.buffer.append(f'<{tag}>{value}</{tag}>')
        self.new_line()

    def text(self) -> str:
        return "".join(self.buffer)
