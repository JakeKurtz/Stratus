in vec3 position;

uniform mat4 view;
uniform mat4 projection;

void main()
{
    gl_Position = projection * vec4(position, 0.001);
    //gl_Position = vec4(position, 1.0);
}