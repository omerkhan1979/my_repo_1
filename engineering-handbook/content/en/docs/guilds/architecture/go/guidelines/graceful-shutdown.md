---
title: "Graceful shutdown"
linkTitle: "Graceful shutdown"
weight: 4
date: 2021-12-17
description: >
  Policies and recommendations for graceful shutdown
---

{{% alert %}}
For proper work of graceful shutdown mechanism it's highly 
encouraged to pass Context everywhere or use done channels 
{{% /alert %}}

## Signal handling & shutdown

Subscribe to termination signals

``` golang
shutdown := make(chan os.Signal, 1)
signal.Notify(shutdown, syscall.SIGINT, syscall.SIGTERM)
```

Example: wait for signal and try to shutdown web server(or any other resources) 

``` golang

func WaitForShutdown(
	log *zap.SugaredLogger, serverErrors chan error, shutdown chan os.Signal,
	shutdownTimeout time.Duration, httpServer *http.Server,
) error {
	select {
	case err := <-serverErrors:
		return fmt.Errorf("server error: %w", err)

	case sig := <-shutdown:
		log.Infow("shutdown", "status", "shutdown started", "signal", sig)
		defer log.Infow("shutdown", "status", "shutdown complete", "signal", sig)

		// Give outstanding requests a deadline for completion.
		ctx, cancel := context.WithTimeout(context.Background(), shutdownTimeout)
		defer cancel()

		// Asking listener to shutdown and shed load.
		if err := httpServer.Shutdown(ctx); err != nil {
			_ = httpServer.Close()

			return fmt.Errorf("could not stop server gracefully: %w", err)
		}
	}

	return nil
}

```
