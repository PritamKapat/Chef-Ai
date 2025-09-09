# TODO: Add Image Upload to AI Scan Button

## Steps to Complete

- [x] Modify generate.html: Update the camera popup "Click" button to capture image from video stream and send as base64 to server.
- [x] Add ai_scan_predict view in views.py: Create a new view that accepts base64 image data, processes it using the CNN model, and returns the predicted class.
- [x] Update urls.py: Add URL pattern for ai_scan_predict view.
- [x] Update JavaScript in generate.html: Handle AJAX response from ai_scan_predict, fill the items input with predicted class, and close popup.
- [x] Test the functionality: Ensure camera capture, prediction, and integration with recipe generation works.

## Notes
- Use canvas to capture image from video.
- Send image as base64 via AJAX POST.
- Process base64 image in view similar to upload_image but without saving file.
- On prediction success, populate the text input and allow user to generate recipe.
