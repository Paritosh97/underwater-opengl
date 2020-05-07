#version 330 core
// ---- camera geometry
uniform mat4 projection, view;

// ---- skinning globals and attributes
const int MAX_VERTEX_BONES=4, MAX_BONES=128;
uniform mat4 boneMatrix[MAX_BONES];

// ---- vertex attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 color;
layout(location = 2) in vec4 bone_ids;
layout(location = 3) in vec4 bone_weights;

// ----- interpolated attribute variables to be passed to fragment shader
out vec3 fragColor;

void main()
{
    // ------ creation of the skinning deformation matrix
    mat4 skinMatrix = mat4(0);

    for (int b=0; b < MAX_VERTEX_BONES; b++)
    skinMatrix +=  bone_weights[b] * boneMatrix[int(bone_ids[b])];

    // ------ compute world and normalized eye coordinates of our vertex
    vec4 wPosition4 = skinMatrix * vec4(position, 1.0);
    gl_Position = projection * view * wPosition4;
    
    fragColor = color;
}