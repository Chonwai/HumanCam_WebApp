module.exports = {
    apps: [
        {
            name: 'HumanCamWebApp',
            instances: 1, // Or a number of instances
            cmd: 'app.py',
            interpreter: 'python3',
            watch: true,
            autorestart: true
        }
    ]
};
