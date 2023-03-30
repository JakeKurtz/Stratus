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

/* -------------------------------- Textures -------------------------------- */

uniform vec2 img_size;
uniform sampler3D noise_tex_3D_32;
uniform sampler3D noise_tex_3D_128;
uniform sampler2D noise_tex_2D_1024;
uniform sampler2D blue_noise;
uniform sampler2D moon_albedo_tex;
uniform sampler2D moon_normal_tex;
uniform sampler2D irra_tex;

out vec4 fragColor;

void main()
{       
    vec2 uv = gl_FragCoord.xy / img_size.xy;

    vec4 x0 = texture(noise_tex_3D_32, vec3(uv,0.0)*32.0);
    vec4 x1 = texture(noise_tex_3D_128, vec3(uv,0.0)*64.0);
    vec4 x2 = texture(noise_tex_2D_1024, uv*16.0);
    vec4 x3 = texture(blue_noise, uv*16.0);
    vec4 x4 = texture(moon_albedo_tex, uv*16.0);
    vec4 x5 = texture(moon_normal_tex, uv*16.0);
    vec4 x6 = texture(irra_tex, uv*16.0);

    fragColor = mix(x0, mix(x1, mix(x2, mix(x3, mix(x4, mix(x5,x6,0.5), 0.5), 0.5), 0.5), 0.5), 0.5);
}