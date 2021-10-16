module.exports = {
    apps: [
        {
            name: 'HumanCamWebApp',
            exec_mode: 'cluster',
            instances: 'max', // Or a number of instances
            script: 'app.py',
            args: 'start',
            watch: true,
            interpreter: 'python3'
        }
    ]
};
