#version 330 core
// ---- camera geometry
uniform mat4 model, view, projection;

// ---- skinning globals and attributes
const int MAX_VERTEX_BONES=4, MAX_BONES=128;
uniform mat4 boneMatrix[MAX_BONES];

// ---- vertex attributes
layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;
layout(location = 2) in vec4 bone_ids;
layout(location = 3) in vec4 bone_weights;
layout(location = 4) in vec2 uvs;

// ----- interpolated attribute variables to be passed to fragment shader
out vec2 frag_tex_coords;
out vec2 frag_uv;

// position and normal for the fragment shader, in WORLD coordinates
out vec3 w_position, w_normal;   // in world coordinates

void main()
{
    // ------ creation of the skinning deformation matrix
    mat4 skinMatrix = mat4(0);

    for (int b=0; b < MAX_VERTEX_BONES; b++)
    skinMatrix +=  bone_weights[b] * boneMatrix[int(bone_ids[b])];

    // ------ compute world and normalized eye coordinates of our vertex
    vec4 wPosition4 = skinMatrix * vec4(position, 1.0);
    gl_Position = projection * view * wPosition4;

    frag_uv = vec2(uvs.x,1-uvs.y);
    frag_tex_coords = position.xy;
    
    // fragment position in world coordinates
    w_position = wPosition4.xyz / wPosition4.w;  // dehomogenize

    // fragment normal in world coordinates
    mat3 nit_matrix = transpose(inverse(mat3(model)));
    w_normal = normalize(nit_matrix * normal);
}