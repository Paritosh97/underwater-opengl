#version 330 core

// fragment position and normal of the fragment, in WORLD coordinates
in vec3 w_position, w_normal;

// light dir, in world coordinates
uniform vec3 light_dir;

// material properties
uniform vec3 k_d, k_a, k_s;
uniform float s;

// world camera position
uniform vec3 w_camera_position;

uniform sampler2D diffuse_map;
in vec2 frag_uv;
out vec4 outColor;

void main() {
    // Compute all vectors, oriented outwards from the fragment
    vec3 n = normalize(w_normal);
    vec3 l = normalize(-light_dir);
    vec3 v = normalize(w_camera_position - w_position);
    vec3 r = reflect(-l, n);
    float diff = max(dot(n, l), 0.0);
    float spec = pow(max(dot(v, r), 0.0), s);

    vec3 ambient_color = k_a * vec3(texture(diffuse_map, frag_uv));
    vec3 diffuse_color = k_d * diff * vec3(texture(diffuse_map, frag_uv));
    vec3 specular_color = k_s * spec * vec3(texture(diffuse_map, frag_uv));

    vec3 result = ambient_color + diffuse_color + specular_color;

    outColor = vec4(result, 1);
}