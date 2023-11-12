const express = require('express');
const { exec } = require('child_process');
const path = require('path');

const app = express();
app.use(express.json());
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

app.get('/home', (req, res) => {
    res.render('home');
});

app.post('/run-command', (req, res) => {
    console.log('BODY', req.body);
    const { command } = req.body;
    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`exec error: ${error}`);
            return res.status(500).send('Internal Server Error');
        }
        console.log(`stdout: ${stdout}`);
        console.error(`stderr: ${stderr}`);
        res.send('Command executed successfully');
    });
});

const PORT = 3111;
app.listen(PORT, () => {
    console.log(`Server listening on port ${PORT}`);
});
