idf_component_register(SRCS "mcpwm_capture_hc_sr04.c"
                    INCLUDE_DIRS "."
                    REQUIRES driver esp_wifi nvs_flash esp_event esp_netif
                    PRIV_REQUIRES esp_http_client mbedtls)
