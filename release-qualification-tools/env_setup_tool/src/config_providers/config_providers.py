from env_setup_tool.src.config_types import Config, CompositeConfig


class BaseConfigProvider:
    """Base class for all config providers.

    This class provides a basic structure for config providers.
    Each derived provider should implement the `apply` method.

    Methods:
        apply: Apply the given configuration.
    """

    def apply(
        self,
        config_data: Config | CompositeConfig,
        subconfig_key: str | None = None,
    ) -> dict[str, bool]:
        """Apply the given configuration.

        This method should be overridden by the derived class.

        Args:
            config_data (dict): The configuration data to be applied.
            subconfig_key (str, optional): config type (See composite config Enums (IMSConfigType, TscConfigType, etc.)
                for full list). If None, all sub-configurations in `config_data` will be applied.

        Raises:
            NotImplementedError: If the method is not implemented by the derived class.
        """
        if isinstance(config_data, Config):
            return self.apply_simple_config(config_data)
        elif isinstance(config_data, CompositeConfig):
            return self.apply_composite_config(config_data, subconfig_key)
        else:
            raise TypeError("Unsupported configuration type")

    def apply_simple_config(self, config_data: Config) -> dict[str, bool]:
        raise NotImplementedError("Subclass must implement apply_simple_config method")

    def apply_composite_config(
        self, config_data: CompositeConfig, subconfig_key: str | None = None
    ) -> dict[str, bool]:
        raise NotImplementedError(
            "Subclass must implement apply_composite_config method"
        )
