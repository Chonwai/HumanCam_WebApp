module.exports = {
    apps: [
        {
            name: 'HumanCamWebApp',
            exec_mode: 'cluster',
            instances: 2, // Or a number of instances
            cmd: 'app.py',
            watch: true,
            autorestart: true,
            interpreter: 'python3'
        }
    ]
};
