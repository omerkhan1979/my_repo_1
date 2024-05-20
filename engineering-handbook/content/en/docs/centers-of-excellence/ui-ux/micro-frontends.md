---
title: "Micro frontends (MFEs)"
date: 2021-11-26
type: blog
weight: 1
author: "Oksana Lugova"
---

# What is a micro-front-end?
Developer Training for Takeoff’s MFEs, UI Components, & Design Tokens: https://drive.google.com/file/d/1Y0J7e-yPW2qexQJhWM-G_HBoDtFbPVU-/view

[Front-End Development Tools @Takeoff](https://docs.google.com/presentation/d/1bQMZBqzLIax3ZwlZb0m7mm0DN9zz8dxfHe-gNQ5S-bA/edit#slide=id.g5f38c73c69_0_198)

A micro-frontend (MFE) extends the concept of microservices on the backend to the frontend layer, breaking down the frontend monolith into smaller, defined, and independent frontend services. Using this architectural approach enables efficiencies and scalable frontend development, particularly across multiple teams.

A micro-frontend approach combined with a microservice architecture delivers end-to-end functionality while allowing for a vertical breakdown of individual systems. Each such vertical can then represent a specific bounded domain context or business problem.

# Building an MFE at Takeoff
See [takeoff-com/mfe-template-repo](https://github.com/takeoff-com/mfe-template-repo) for step by step instructions on how to build a Micro-Front-End at Takeoff.

While building your MFE you may find that some of UI elements could be reusable in other MFEs. Feel free to develop those elements directly in your MFE repo. This will let you more quickly get feedback from real-world use cases. Once it is working the way you like, and if you think it's developed in a reusable way, [feel free to contribute it to Core-UI]({{< relref "./creating-a-new-shared-component.md" >}}). Contributing it to Core-UI immediately is not a requirement. Just because the component could be reusable, does not mean we need to make it that way from day one.

If you’re building an MFE that could reuse a UI element from some other page, and that element isn’t in Core-UI, work with the team that owns the MFE to understand how it works and who has capacity to extract the component to Core-UI. If the team that owns the original MFE does not have capacity, that's OK! We all have access to GitHub and can work together to make the system better without blocking each other. If your team also does not have capacity to do such refactoring, do you have the capacity to develop the MFE in the first place?

Remember: Let the code decide! Do not refactor until you need to. Do not turn our MFE ecosystem into a distributed monolith by making every change require edits to Core-UI.
