## Key Classes
==
[[Table of Contents](../../README.md#table-of-contents)] : [Getting Started](../../getting-started/00-getting-started.md)

### WavePlanner
Waves are needed for picking. `test_wave_planner.py` was created to work with test 
cases to assist in creating the necessary waves for test cases. A
fixture called `wave_planner` and can be used to create the necessary waves for
test case implementation. 

***Troubleshooting***

```
Exception during GET request to https://wave-planner.ode.outbound.chavess.ode.takeofftech.org/v1/retailers/maf/mfcs/D02/wavePlan

<html><head>
<meta http-equiv="content-type" content="text/html;charset=utf-8">
<title>404 Page not found</title>
</head>
<body text=#000000 bgcolor=#ffffff>
<h1>Error: Page not found</h1>
<h2>The requested URL was not found on this server.</h2>
```

If you are seeing a message that the wave plan for the retailer doesn't exist or the wave plan for the MFC doesn't exist.
For ODE environments, make sure the <code>RETAILER_PROJECT_NAME</code> evironment variable is set up correctly.