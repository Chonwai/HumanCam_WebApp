module.exports = {
    apps: [
        {
            name: 'HumanCamWebApp',
            instances: 2, // Or a number of instances
            cmd: 'app.py',
            interpreter: 'python3',
            watch: true,
            autorestart: true,
        }
    ]
};
