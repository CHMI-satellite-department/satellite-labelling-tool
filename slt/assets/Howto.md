## About this app
A tool for manual labeling of storm top features such as overshooting tops, above-anvil plumes, cold U/Vs, rings etc.
This app is based on [Dash Bounding Box Image Annotation](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-image-annotation) app, which demonstrates how Dash can be used to annotate and classify areas in an image. This app is using its features and optimaze it for labelling satellite images.
You can:
- freehand draw rectangles to highlight areas of the satellite images
- classify the highlighted areas with a label of storm top features
- edit the higlighted areas 
- see the information on highlighted areas in an interactive table
- select different images to annotate
- export the annotations you have made

## How to use this app
To annotate the image, first select the annotation label you want to apply, then select annotator: 
![Screenshot of label selector](assets/select_label_slt.png)
![Screenshot of label selector](assets/select_annotator_slt.png)

You can zoom in to find details:
![Screenshot of label selector](assets/zoom.png)

Then draw a rectangle on the image area you want to annotate with your cursor:
![Screenshot of bounding box](assets/draw_annotation_slt.png)

You can continue annotating additional areas of the image, selecting a different image with the `previous` and `next`
buttons, or you can download the annotations and use them to train an image content classifier:
![Screenshot of download](assets/download_annotation_slt.png)
