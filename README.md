# Robotic-Guard-Dog
Robotic Guard Dog 


CV-Enhanced Pupper Robot as a Responsive Guard Dog

1. Problem Description:
In the modern world, issues regarding home security and area surveillance are of major concern. Currently, security systems tend to be passive, and they tend to focus mainly on processes of monitoring versus processes of action and reaction. This limitation becomes more pronounced in scenarios where an interactive response could enhance security measures and deter intruders. Thus, an intelligent, interactive response system resolves a critical gap in personal security scenarios. Ideally, a system would be able to not only observe, but also interpret human body language and respond in a meaningful way. We aim to utilize the Pupper robot for this purpose.

2. Proposed Solution:
To address this problem, this project proposes the development of an AI-driven Pupper robot, which acts as an interactive guard dog, capable of interpreting and responding to human body language. The core of this system lies in the integration of computer vision techniques, enabling the robot to distinguish between various human stances and postures, identify them as threatening or nonthreatening, and act on it. We will use open source pose tracking models to enable the robot to identify specific gestures, like raised hands or aggressive stances. This recognition capability will be paired with responsive actions by the robot, such as adopting a non-threatening posture (lying down) when a person shows a surrender stance, or assuming an alert stance in response to a perceived threat.

3. Expected Results:
Our baseline to demo is for pupper to detect and differentiate basic threatening poses. Pupper should be able to detect a threatening person as someone who has their hands apart and a non-threatening person as someone who has their hands together. Pupper should perform this in real time and perform some action accordingly to the detected action. It should sit during a non-threatening pose. It should stand during a threatening pose and (if an audio output is available) start barking. Pupper should be able to smoothly alternate between the behaviors. As reach-goals, we would have pupper detect and respond to dangerous objects (e.g. fork) and poses (e.g. finger gun) accordingly with additional behaviors.

4. Milestones:
Milestone 0: Set up the development environment.

Milestone 1: Building off existing computer vision framework, incorporate detection for open- and closed-armed poses, printing output

Milestone 2: Develop pupper response stances according to detected poses. 
