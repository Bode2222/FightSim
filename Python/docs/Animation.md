How To Make A Torque-Based Ragdoll
Overview

Creating a torque-driven ragdoll involves applying constant forces to each bone or body part, coupled with specific joint constraints. The goal is to simulate realistic physics for characters in a game engine.
Integration with IK Targets

To integrate torque-based ragdoll with IK targets for posing and animation, a "physical rig" or hit engine can be implemented. This conduit for forces manages the impact of hits on the ragdoll.
Hit Processing

    When hit, add force (torque) to a force list on the ragdoll.
    Queue actions are fed into the procedural animation engine.

Procedural Animation Engine

    Calculates ideal bone rotations each frame based on queued actions.
    Outputs a base pose.

Physical Animation Engine

    Takes the base pose from the procedural engine.
    Applies a 'base force' to ensure output rotations match procedural engine rotations.
    Applies all forces in the force list, where forces on the root bone move the entire model.

This hit engine manages the impact response, procedural animation, and physical animation.
Questions and Challenges

    Inertia:
        How to ensure the model exhibits inertia, reacting realistically to external forces such as getting kicked in the stomach.

    Force to Bone Rotations:
        How to convert a force applied to a body part into bone rotations.

Solutions

To address these challenges:
Separate Pose Engine

    Implement the hit engine as a separate component from the main game engine.
    Utilize external tools like Blender for realistic physics calculations.
    Import the hit engine as a dependency, providing required inputs and obtaining body positions for each agent.
    Set IK targets to corresponding body parts for motion calculations.

By structuring the solution in this way, you can maintain a clear separation between the torque-based ragdoll simulation and the broader game engine. The pose engine, responsible for updating the display, receives information on desired actions, landed hits, and current positioning. This design allows independent decision-making for characters, with their knowledge limited to IK targets and opponents' weak points. The environment will have each characters skeleton, the character will give the environment it's desired actions, the environment will calculate which hits landed on the character. The environment will give the pose engine the actions the character wants performed, the hits landed and the current pose of the character, the pose engine will then update the skeleton and pass it to the display engine, which can finally display the character. This way a fight can start with positions given to the environment by the user.