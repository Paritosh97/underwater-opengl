import OpenGL.GL as GL

class Particles:
    
    def __init__(self):
        self.position = 0
        self.velocity = 0
        self.color = 0
        self.life = 0
"""
    def draw(self, projection, view, model):
        glBlendFunc(GL_SRC_ALPHA, GL_ONE);
        particleShader.Use();
        for (Particle particle : particles)
        {
            if (particle.Life > 0.0f)
            {
                particleShader.SetVector2f("offset", particle.Position);
                particleShader.SetVector4f("color", particle.Color);
                particleTexture.Bind();
                glBindVertexArray(particleVAO);
                glDrawArrays(GL_TRIANGLES, 0, 6);
                glBindVertexArray(0);
            } 
        } 
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
"""