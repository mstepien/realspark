# ImageAnalysisApi.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**getStats**](DefaultApi.md#getStats) | **GET** /stats | Get aggregate statistics of analyzed images
[**getTaskStatus**](DefaultApi.md#getTaskStatus) | **GET** /progress/{task_id} | Get the status of an image analysis task
[**startUpload**](DefaultApi.md#startUpload) | **POST** /upload | Upload an image for analysis



## getStats

> AggregateStats getStats()

Get aggregate statistics of analyzed images

### Example

```javascript
import ImageAnalysisApi from 'image_analysis_api';

let apiInstance = new ImageAnalysisApi.DefaultApi();
apiInstance.getStats((error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters

This endpoint does not need any parameter.

### Return type

[**AggregateStats**](AggregateStats.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## getTaskStatus

> TaskStatus getTaskStatus(taskId)

Get the status of an image analysis task

### Example

```javascript
import ImageAnalysisApi from 'image_analysis_api';

let apiInstance = new ImageAnalysisApi.DefaultApi();
let taskId = "taskId_example"; // String | 
apiInstance.getTaskStatus(taskId, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **taskId** | **String**|  | 

### Return type

[**TaskStatus**](TaskStatus.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: Not defined
- **Accept**: application/json


## startUpload

> UploadResponse startUpload(opts)

Upload an image for analysis

### Example

```javascript
import ImageAnalysisApi from 'image_analysis_api';

let apiInstance = new ImageAnalysisApi.DefaultApi();
let opts = {
  'sessionId': "sessionId_example", // String | Session ID for tracking and abandoning previous tasks.
  'file': "/path/to/file" // File | 
};
apiInstance.startUpload(opts, (error, data, response) => {
  if (error) {
    console.error(error);
  } else {
    console.log('API called successfully. Returned data: ' + data);
  }
});
```

### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **sessionId** | **String**| Session ID for tracking and abandoning previous tasks. | [optional] 
 **file** | **File**|  | [optional] 

### Return type

[**UploadResponse**](UploadResponse.md)

### Authorization

No authorization required

### HTTP request headers

- **Content-Type**: multipart/form-data
- **Accept**: application/json

