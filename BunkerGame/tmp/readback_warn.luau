local mp = game:GetService('Workspace'):FindFirstChild('ArgonProof')
mp = mp and mp:FindFirstChild('ArgonProofMeshPart01')
if mp then
  warn('ARGONPROOF6| MESHID=' .. tostring(mp.MeshId))
  warn('ARGONPROOF6| SIZE=' .. tostring(mp.Size))
  warn('ARGONPROOF6| POSITION=' .. tostring(mp.Position))
  warn('ARGONPROOF6| ANCHORED=' .. tostring(mp.Anchored))
  warn('ARGONPROOF6| CANCOLLIDE=' .. tostring(mp.CanCollide))
  warn('ARGONPROOF6| MASSLESS=' .. tostring(mp.Massless))
else
  warn('ARGONPROOF6| NO_MESH_PART')
end
warn('ARGONPROOF6| DONE')