using Pkg
site = ARGS[1]
# Common dependencies used across the roadmap's original notebooks.
core = ["IJulia", "PyPlot", "Plots", "Interact", "Symbolics", "SymPy",
        "Images", "FileIO", "ImageMagick", "QuadGK", "Polynomials", "FFTW",
        "ForwardDiff", "BenchmarkTools", "KrylovKit", "IterativeSolvers"]
# Specialized graph, optimization and ML examples can install these on demand.
extras = ["RowEchelon", "Graphs", "MetaGraphs", "GraphPlot", "NamedColors",
          "Flux", "ImageShow", "JuMP", "Ipopt"]
if isfile(joinpath(site, "julia", "Manifest.toml"))
    Pkg.instantiate()
else
    Pkg.add(core)
end
if "--extras" in ARGS
    Pkg.add(extras)
end
# PyPlot and SymPy reuse our Python environment, never a separate global Conda.
Pkg.build("PyCall")
using IJulia
IJulia.installkernel("Julia 18.06", "--threads=1,0", "--project=$(joinpath(site, "julia"))",
    specname="julia-1806", env=Dict(
        "JULIA_DEPOT_PATH" => joinpath(site, ".runtime", "julia-depot"),
        "JULIA_NUM_THREADS" => "1", "OPENBLAS_NUM_THREADS" => "2",
        "JUPYTER" => joinpath(site, ".venv", "bin", "jupyter"),
        "PYTHON" => joinpath(site, ".venv", "bin", "python"),
        "MPLCONFIGDIR" => joinpath(site, ".runtime", "matplotlib"),
        "MPLBACKEND" => "Agg", "GKSwstype" => "100",
    ))
println("Julia 18.06 kernel registered.")
