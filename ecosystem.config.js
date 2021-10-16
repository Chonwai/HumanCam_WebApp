module.exports = {
    apps: [
        {
            name: 'HumanCamWebApp',
            exec_mode: 'cluster',
            instances: 2, // Or a number of instances
            // script: 'app.py',
            args: 'app.py',
            watch: true,
            interpreter: 'python3'
        }
    ]
};
