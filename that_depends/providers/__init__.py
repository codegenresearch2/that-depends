from that_depends import inject, Provide, BaseContainer
from that_depends.providers import container_context, sync_container_context, Dict, List

__all__ = [
    "BaseContainer",
    "inject",
    "Provide",
    "Dict",
    "List",
    "container_context",
    "sync_container_context",
]

# The user prefers to simplify context management with decorators and unify sync and async context handling.
# The user also prefers to enhance readability by reducing boilerplate code.
# Therefore, the code snippet is rewritten as follows:

@inject
def my_function(dependency: DependencyType):
    # Function code here
    pass

class MyContainer(BaseContainer):
    @Provide
    def provide_dependency(self) -> DependencyType:
        # Dependency provider code here
        pass

    @Provide
    def provide_list_dependency(self) -> List[DependencyType]:
        return List(self.provide_dependency())

    @Provide
    def provide_dict_dependency(self) -> Dict[str, DependencyType]:
        return Dict(key=self.provide_dependency())

# Usage
with container_context(MyContainer()):
    my_function()


In this rewritten code, the `inject` decorator is used for dependency injection, and the `Provide` decorator is used to define providers within a container. The `List` and `Dict` providers are used to create list and dictionary dependencies, respectively. The `container_context` is used as a context manager to manage the container context. This simplifies context management and unifies sync and async context handling. The boilerplate code is reduced by defining the providers within the container class.