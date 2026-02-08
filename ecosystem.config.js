module.exports = {
  apps: [
    {
      name: 'fte-watcher',
      script: 'watchers/filesystem_watcher.py',
      interpreter: 'python3',
      cwd: '/Volumes/Macintosh HD/DigitalFTE',
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 5000,
      env: {
        VAULT_PATH: '/Volumes/Macintosh HD/DigitalFTE/AI_Employee_Vault',
        DRY_RUN: 'false',
        LOG_LEVEL: 'INFO'
      },
      error_file: '/tmp/fte-watcher-error.log',
      out_file: '/tmp/fte-watcher-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true
    }
  ]
};
