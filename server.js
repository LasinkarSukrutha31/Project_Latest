const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const csv = require('csv-parser');
const cors = require('cors');
const app = express();
const port = 5004;

// Middleware to parse JSON data and allow cross-origin requests
app.use(bodyParser.json());
app.use(cors()); // Enable CORS for all origins
app.use(express.static('public')); // Serve static files like HTML

// Register endpoint to handle user registration
app.post('/register', (req, res) => {
  const { username, aadhar, phone, password } = req.body;

  const newUser = `${username},${aadhar},${phone},${password}\n`;

  // Append new user to the CSV file
  fs.appendFile('data.csv', newUser, (err) => {
    if (err) {
      return res.status(500).json({ success: false, message: "Failed to register" });
    }
    res.json({ success: true, message: "User Registered Successfully!" });
  });
});

// Login endpoint to check user credentials
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  
  let foundUser = false;

  // Read the CSV file and check for matching credentials
  fs.createReadStream('data.csv')
    .pipe(csv())
    .on('data', (row) => {
      // Trim spaces and check if the username and password match
      if (row.username.trim() === username.trim() && row.password.trim() === password.trim()) {
        foundUser = true;
      }
    })
    .on('end', () => {
      if (foundUser) {
        res.json({ success: true, message: `Welcome ${username}!` });
      } else {
        res.json({ success: false, message: "Invalid credentials, please register first." });
      }
    });
});

// Start the server
app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
