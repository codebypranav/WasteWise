#include "esp_http_client.h"
#include "esp_log.h"
#include "cJSON.h"

#define BACKEND_URL "http://192.168.0.115:5000/api/current-stats"  // Replace X.X with your laptop's IP

esp_err_t send_measurement(float fill_level) {
    esp_http_client_config_t config = {
        .url = BACKEND_URL,
        .method = HTTP_METHOD_POST,
    };
    
    esp_http_client_handle_t client = esp_http_client_init(&config);
    
    // Create JSON payload
    cJSON *root = cJSON_CreateObject();
    // Assuming this is non-recyclable waste - adjust as needed
    cJSON_AddNumberToObject(root, "non_recyclable", fill_level);
    cJSON_AddNumberToObject(root, "recyclable", 0);
    cJSON_AddNumberToObject(root, "organic", 0);
    cJSON_AddNumberToObject(root, "temperature", 25.0); // Add actual temperature if available
    
    char *post_data = cJSON_Print(root);
    
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, post_data, strlen(post_data));
    
    esp_err_t err = esp_http_client_perform(client);
    
    if (err == ESP_OK) {
        ESP_LOGI("HTTP", "Data sent successfully");
    } else {
        ESP_LOGE("HTTP", "Failed to send data");
    }
    
    free(post_data);
    cJSON_Delete(root);
    esp_http_client_cleanup(client);
    
    return err;
}