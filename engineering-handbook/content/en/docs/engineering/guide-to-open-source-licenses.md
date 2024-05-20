---
title: "Guide - Open Source Licenses"
linkTitle: "Open Source Licenses Guide"
date: 2023-11-21
weight: 9
description: >
  A detailed guide to open source licenses for dependencies used in project. 
---
![open-source-licenses](/images/en/docs/Engineering/open_source_licenses/page_banner.png)

### Recommended Guidelines for licenses
<table>
<tbody>

<tr>
<th style="background-color: #57d9a3"> Preferred Licenses (Permissive) - No approval needed </th>
<th style="background-color: #ffc400"> Weak Copyleft Licenses - Needs approval </th>
<th style="background-color: #ff8f73"> Prohibited Licenses (Strong Copyleft) - Needs exception </th>
</tr>

<tr>
<td style="background-color: #abf5d1">MIT License</td>
<td style="background-color: #fff0b3">Mozilla Public License (MPL)</td>
<td style="background-color: #ffbdad">GNU General Public License - GPL</td>
</tr>

<tr>
<td style="background-color: #abf5d1">Apache License 2.0</td>
<td style="background-color: #fff0b3">Eclipse Public License (EPL)</td>
<td style="background-color: #ffbdad">Affero General Public License - AGPL</td>
</tr>

<tr>
<td style="background-color: #abf5d1">BSD 3-Clause License</td>
<td style="background-color: #fff0b3">Microsoft Reciprocal License (MsRL)</td>
<td style="background-color: #ffbdad">GNU Lesser General Public License - LGPL</td>
</tr>

</tbody></table>

### Open-source software

An Open-source software is an application or program for which the actual **source code** is made available publicly. 
If the software is Open-source, its source code can be accessed by anyone to view, copy, change, improve, and share it with others. 
This is the reason most of the open-source software is developed by communities and in a collaborative way rather than a single developer or company.
[Open Source Initiative (OSI)](https://opensource.org/) is an organisation that promotes the usage of Open-source Software.

{{% alert title="Copyright and License" %}}
In its simplest terms, Copyright and License can be defined as follow:

**Copyright** is the legal term used to show and prove who owns the product or software.

**License** is defined as an agreement, wherein a company/organization authorizes another party/user to use its product under certain terms.

In layman’s terms, if you own a property/house, the ownership documents or a “deed” is the copyright.
This proves your ownership. And when you consider renting out your house, you make a rental agreement with the tenant.
That agreement is a License where you authorize your tenant to use your house under certain terms.
{{% /alert %}}

{{% alert title="Categories of Licenses" %}}
Broadly categorizing the licenses, we will talk about Creative Commons License **Vs** Permissive License **Vs** Copyleft License **Vs** Proprietary License. These licenses define the rules as to how someone’s software/work may be used by any user or organization.

<img alt="Categories of Licenses" src="/images/en/docs/Engineering/open_source_licenses/license_categories.png" width="900"/>
There are very few or no restrictions with the Creative Commons License. The licenses become more restrictive as we move from the left to right side in the picture.

1. **Creative Commons License**
If you want to release your software or work to the public domain (make it freely available and with no copyrights), it is recommended to use CC0. The [Creative Commons CC0](https://creativecommons.org/share-your-work/public-domain/cc0/) license is used to put software into the public domain. Any software or work that is released under CC0 is dedicated to the public domain which means anyone can do anything with it. There are no restrictions, and the original author/developer of the work has waived all rights. You can copy, modify, and redistribute it as you wish.


2. **Permissive License**
A permissive license is a BSD-like or BSD-style license which is a free software license with minimal restrictions on how software could be used, modified, or redistributed. They require attribution to original authors in derivative work or source code. The Derivative work can be released under another license or as proprietary software. Examples include the **MIT License**, **BSD license**, **Apple Public Source License**, and **Apache license**.
[BSD License](https://opensource.org/licenses/BSD-3-Clause) which is a permissive license may contain 4 or fewer clauses. The main benefit of using a BSD license is that it doesn’t require the user to redistribute the code or derivative work. This is a must in Copyleft License.

3. **Copyleft License**
This is the same license that we have discussed above. It is a more restrictive license and states that anyone who uses the original source code to build something must also redistribute the derivative work under the same license. Copyleft guarantees that every user has freedom. If the software is licensed under a copyleft license, the derivative work must be redistributed under the same license terms. The first and most popular example of a **Copyleft license is GNU GPL**.

4. **Proprietary License**
The proprietary software license doesn’t allow copying, modifying, or redistribution. This is the most restrictive license. The original author or the company who releases the software or work retains copyrights of the source code. Usually, the source code is hidden from the end-users and doesn’t grant rights to modify the software in any way or redistribute it.
{{% /alert %}}

   
#### <<WIP>> Role of the Open-source / Third-party software Review Board (OSRB)

Open-source/ Third-party software Review Board (OSRB) is a team comprised of members responsible for establishing and reviewing licensing terms as well as reviewing against known security vulnerabilities before adopting new OS libraries/components. 
This role can also be performed by the engineering guild committee.
The OSRB also provides strategy, communication and guideline manuals (set of rules and regulations to be followed) for developers in organisation. It also consists of the following aspects to regulate the use of OSS licenses -

1. **Recommended Guidelines**
Any open source component licensed under the preferred licenses can be freely used without additional disclosure or approval by the OSRB.


**Top open source licenses – a cheat sheet**

<table>
<tbody>

<tr>
<th></th>
<th>Type</th>
<th>Popularity</th>
<th>How to comply</th>
<th>Risk</th>
</tr>

<tr>
<th>MIT License</th>
<td>Permissive licenses</td>
<td>Very popular</td>
<td>Add a cop of the original MIT license and copyright notice</td>
<td>Low</td>
</tr>

<tr>
<th> Apache License 2.0 </th>
<td>Permissive licenses</td>
<td>Very popular</td>
<td>Include required notices</td>
<td>Low</td>
</tr>

<tr>
<th> BSD 2.0 </th>
<td>Permissive licenses</td>
<td>Not very popular</td>
<td>Include the copyright notice</td>
<td>Low</td>
</tr>

<tr>
<th> BSD 3.0 </th>
<td>Permissive licenses</td>
<td>Not very popular</td>
<td>Include the copyright notice</td>
<td>Low</td>
</tr>

<tr>
<th> ISC License </th>
<td>Permissive licenses</td>
<td>Not very popular</td>
<td>Include the original copyright notice</td>
<td>Low</td>
</tr>

<tr>
<th> MPL 1.1 </th>
<td>Semi-premissive licenses</td>
<td>Rare</td>
<td>Include a notice in each source file</td>
<td>Medium</td>
</tr>

<tr>
<th> CDDL </th>
<td>Semi-premissive licenses</td>
<td>Rare</td>
<td>Original and modified source code made available under CDDL</td>
<td>Medium</td>
</tr>

<tr>
<th> Microsoft Public License </th>
<td>Semi-premissive licenses</td>
<td>Rare</td>
<td>Link the license and existing copyrights</td>
<td>Medium</td>
</tr>

<tr>
<th> GPL 2.0 </th>
<td>Copyleft licenses</td>
<td>Very popular</td>
<td>Modifications must be made available under GPL</td>
<td>High</td>
</tr>

<tr>
<th> GPL 3.0 </th>
<td>Copyleft licenses</td>
<td>Popular</td>
<td>Modifications must be made available under GPL</td>
<td>High</td>
</tr>

<tr>
<th> AGPL 3.0 </th>
<td>Copyleft licenses</td>
<td>Not very popular</td>
<td>You must license derivatives under AGPL</td>
<td>High</td>
</tr>

<tr>
<th> LGPL 2.1 </th>
<td>Lesser general public licenses</td>
<td>Rare</td>
<td>Components statically linked can be redistributed under LGPL, while apps don't have to</td>
<td>High</td>
</tr>

<tr>
<th> LGPL 3.0 </th>
<td>Lesser general public licenses</td>
<td>Rare</td>
<td>Components statically linked can be redistributed under LGPL, while apps don't have to</td>
<td>High</td>
</tr>

</tbody></table>


2. **Approval Process**
We should set up a process to identify, review, leverage, manage, and distribute components associated with diverse open source licenses. With this process in place, we can identify risks and regulations associated with OSS licenses and also gain other benefits including accelerated delivery schedules and preemptive actions to mitigate risks or surplus costs.
   1. Developers must receive approval from the OSRB by submitting the request before integrating any open source/third-party libraries/components other than the preferred licenses specified above
   2. The software received from third parties must be audited to identify any open source code included, which ensures license obligations
   3. Our software must be audited and reviewed to identify the security vulnerabilities
   4. All new major versions of specific component must go through the approval process

### Is it risky to use open source software?

Permissive open source licenses generally allow us to use an open source component freely as long as we maintain any copyright notices. But if we use a component with a restrictive license in our proprietary software, we might be legally obligated to release our software under the same license (i.e., as royalty-free open source software). As long as we are managing our use of open source (i.e., we know what's in our codebase and what kind of licenses are attached), we can manage our legal risk.

### What kind of open source license risks are there?

There are many ways to categorize open source license risks. Our software audits group classifies risks based on priority. For example, some licenses in our codebase might be OK to use as is, but others might be in conflict with other licenses, so we need to research them before proceeding. We further classify risks based on type of license (e.g., permissive or restrictive), which reflects our legal exposure if we use components that have those licenses.

Our guide to the top open source licenses lists some of the most popular open source licenses according to these risk categories:

**Low risk** - Permissive licenses are consider low risk because it's easy to meet their reuse requirements: Usually we just have to retain the copyright notice, but we don't have to expose our source code. Examples are the Apache and MIT Licenses.

**Medium risk** - Semi-permissive licenses, sometimes referred to as limited licenses, weak copyleft licenses, or simple copyleft licenses, are considered medium risk because if we modify the code, we have to release the modifications, but not our whole application, under the same license. Different licenses define "modification" differently. Examples are the Mozilla and the Eclipse Public Licenses.

**High risk** - Restrictive licenses carry a great deal of legal risk. If we use a component with one of these licenses, we might be legally obligated to release our entire application code. Examples are the GNU GPL and GNU LGPL.
