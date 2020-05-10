#version 330 core

uniform sampler2D diffuse_map;
in vec2 frag_uv;
out vec4 outColor;

void main() {
    outColor = texture(diffuse_map, frag_uv);
}