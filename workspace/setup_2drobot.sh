#!/bin/bash
cd
# ROS 2 Humble's cv_bridge and system Matplotlib require the NumPy 1.x ABI.
pip install "numpy<2" ultralytics
# Clone the base line repository for the 2D robot practice workspace
git clone https://github.com/OsawaKousei/2DRoboPrac_ws
cd 2DRoboPrac_ws/gz_ws/MakeYourRobot/models
ign gazebo /workspace/world.sdf