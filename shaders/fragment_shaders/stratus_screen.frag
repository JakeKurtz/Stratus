/* ------------------------------------------------------------------------- *
*
*    Copyright (C) 2023 Jake Kurtz
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
*    GNU General Public License for more details.
*
*    You should have received a copy of the GNU General Public License
*    along with this program. If not, see <https://www.gnu.org/licenses/>.
*
* ------------------------------------------------------------------------- */

out vec4 fragColor;

uniform sampler2D tex;

uniform vec2 monitor_size;
uniform vec2 scr_size;
uniform vec2 tex_size;

uniform mat4 inv_vp_mat;
uniform float env_img_strength;

uniform float gamma = 1.0;

vec3 sat(vec3 v)
{
    return clamp(v, vec3(0.0), vec3(1.0));
}

vec3 reinhard(vec3 x)
{
    vec3 col = x / (vec3(1.0) + x);
    return col;
}

void main() 
{
    vec2 uv = gl_FragCoord.xy / scr_size;   
    uv *= tex_size / monitor_size;

    vec3 texColor = texture(tex, uv).rgb * env_img_strength;

    vec3 color = sat(reinhard(texColor));

    color = pow(color, vec3(1.0 / gamma));

    fragColor = vec4(color, 1.0);
}