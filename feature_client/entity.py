from dataclasses import dataclass


@dataclass
class FeatureFlag:
    name: str
    enabled: bool
