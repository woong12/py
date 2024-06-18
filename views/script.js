// Function to fetch and display webcam feed
function displayWebcamFeed() {
  // Endpoint URL for fetching webcam feed
  // const webcamFeedUrl = "http://10.251.150192.168.0.39:8000/index.html.148:8000/stream.mjpg"; // Replace with your actual RPI cam server address and port
  const webcamFeedUrl = "http://192.168.0.39:8000/stream.mjpg"; // Replace with your actual RPI cam server address and port

  // Select the div where you want to display the webcam feed
  const webcamFeedDiv = document.getElementById("cameraPi");

  // Create a new HTML <img> element to display the webcam feed
  const webcamImage = document.createElement("img");

  // Set attributes for the image element
  webcamImage.src = webcamFeedUrl; // Set the source of the image to the webcam feed URL
  webcamImage.alt = "Webcam Feed"; // Provide an alt attribute for accessibility

  // Append the image element to the webcam feed div
  webcamFeedDiv.appendChild(webcamImage);
}