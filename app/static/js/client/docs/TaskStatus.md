# ImageAnalysisApi.TaskStatus

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**status** | **String** | Current status (Starting..., Preprocessing..., Performing Parallel Analysis &amp; Upload..., Saving to Database..., Complete, Error, Abandoned) | 
**progress** | **Number** |  | 
**steps** | **[String]** |  | 
**currentStep** | **String** |  | [optional] 
**completedSteps** | **[String]** |  | 
**partialResults** | **{String: Object}** |  | [optional] 
**result** | [**TaskStatusResult**](TaskStatusResult.md) |  | [optional] 
**error** | **String** | Error message if the task failed (e.g., due to analysis error or process timeout). | [optional] 


