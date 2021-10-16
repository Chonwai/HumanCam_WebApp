module.exports = {
    apps: [
        {
            name: 'HumanCamWebApp',
            exec_mode: 'cluster',
            instances: 2, // Or a number of instances
            script: 'app.py',
            args: 'start',
            watch: true,
            interpreter: 'python3'
        }
    ]
};
