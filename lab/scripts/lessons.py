LESSONS = [
 dict(title='认识你的线性代数计算器', short='NumPy 最小准备', group='准备', lead='从一个矩阵和一个向量开始。先预测结果，再让 Python 验证你的直觉。', formula=r'Ax=\begin{bmatrix}1&2\\3&4\end{bmatrix}\begin{bmatrix}1\\1\end{bmatrix}=\begin{bmatrix}3\\7\end{bmatrix}', concept='NumPy 的数组记录数字与形状。`@` 表示矩阵乘法，`*` 表示逐元素相乘。一维数组只有长度，转置不会自动把它变成二维列向量。', challenge='把 x 改成 [2., -1.]，运行前先预测 A @ x。再把 x 改为列向量，观察输出形状。', lectures=[1], code='''import numpy as np

A = np.array([[1., 2.], [3., 4.]])
x = np.array([1., 1.])

print("A 的形状：", A.shape)
print("Ax =", A @ x)
print("逐元素乘法：\\n", A * A)
print("矩阵乘法：\\n", A @ A)
print("一维 x / x.T：", x.shape, x.T.shape)
print("二维列向量：", x[:, None].shape)
'''),
 dict(title='把方程看成列的组合', short='Ax = b 与消元', group='方程与空间', lead='解方程，是寻找一组系数，让矩阵的列恰好组合成目标向量。', formula=r'Ax=x_1a_1+x_2a_2=b', concept='对于 m×n 矩阵，输入有 n 个坐标，输出有 m 个坐标。消元把原方程换成更容易回代、但解相同的方程。', challenge='把 b 改成 [3., 4.]，重新手算解。对照列组合与矩阵乘法，解释它们为何得到相同结果。', lectures=[1,2,3], code='''import numpy as np

A = np.array([[2., 1.], [1., 3.]])
b = np.array([1., 2.])
x = np.linalg.solve(A, b)

print("系数 x：", x)
print("列的组合：", x[0]*A[:, 0] + x[1]*A[:, 1])
print("Ax：", A @ x)
print("残差：", A @ x - b)
assert np.allclose(A @ x, b)
'''),
 dict(title='消元的背后是一次分解', short='LU 与奇异矩阵', group='方程与空间', lead='把消元步骤记录下来，就得到 L；消元后的上三角矩阵就是 U。', formula=r'A=LU,\qquad Lc=b,\quad Ux=c', concept='遇到零主元可能只需换行，不代表矩阵必定不可逆。需要换行时，用置换矩阵 P 记录顺序，可写作 PA=LU。', challenge='试着对 [[0.,1.],[1.,1.]] 交换两行，解释新矩阵为什么可以从第一个主元开始消元。', lectures=[2,3], code='''import numpy as np

A = np.array([[2., 1.], [1., 3.]])
L = np.array([[1., 0.], [0.5, 1.]])
U = np.array([[2., 1.], [0., 2.5]])
E = np.array([[1., 0.], [-0.5, 1.]])
b = np.array([1., 2.])
c = np.linalg.solve(L, b)
x = np.linalg.solve(U, c)
print("LU 还原 A：", np.allclose(L @ U, A))
print("EA 等于 U：", np.allclose(E @ A, U))
print("分两次求得 x：", x)

B = np.array([[1., 2.], [2., 4.]])
for rhs in ([3., 6.], [3., 7.]):
    fit = np.linalg.lstsq(B, rhs, rcond=None)[0]
    print("b =", rhs, "最小残差 =", np.linalg.norm(B @ fit-rhs))
'''),
 dict(title='秩数的是独立方向', short='基、秩与全部解', group='方程与空间', lead='三列不一定代表三个方向。这个矩阵把整个三维输入空间压到一条直线上。', formula=r'x=\begin{bmatrix}1\\0\\0\end{bmatrix}+s\begin{bmatrix}-2\\1\\0\end{bmatrix}+t\begin{bmatrix}-3\\0\\1\end{bmatrix}', concept='主元数等于秩；自由变量给出零空间的维数。若一个解已知，加上任何零空间向量仍然是解。列空间的基要从原矩阵选。', challenge='改变 s、t，观察 Ax 是否变化。把 b 改成 [1.,3.]，用列空间解释为什么无解。', lectures=[4,5,6,7], code='''import numpy as np

A = np.array([[1., 2., 3.], [2., 4., 6.]])
x0 = np.array([1., 0., 0.])
z1 = np.array([-2., 1., 0.])
z2 = np.array([-3., 0., 1.])
s, t = 2., -1.
x = x0 + s*z1 + t*z2

print("秩：", np.linalg.matrix_rank(A))
print("两个零空间方向：", A @ z1, A @ z2)
print("本次选择的解：", x)
print("Ax：", A @ x)
assert np.allclose(A @ x, [1., 2.])
'''),
 dict(title='一个矩阵，四个空间', short='四个基本子空间', group='方程与空间', lead='把输入与输出分开考虑：哪些方向被保留，哪些方向被压到零，哪些输出无法到达？', formula=r'\mathbb R^n=C(A^T)\oplus N(A),\qquad\mathbb R^m=C(A)\oplus N(A^T)', concept='行空间与零空间同在输入端，是正交补；列空间与左零空间同在输出端，也是正交补。两端环境的维数可能不同。', challenge='换用一个 3×2 矩阵，先写四个空间的环境维数，再计算 rank 并写出四个维数。', lectures=[8,9], code='''import numpy as np

A = np.array([[1., 2., 3.], [2., 4., 6.]])
row = np.array([1., 2., 3.])
null = np.array([[-2., 1., 0.], [-3., 0., 1.]])
column = np.array([1., 2.])
left_null = np.array([-2., 1.])
m, n = A.shape
r = np.linalg.matrix_rank(A)
print("列 / 零 / 行 / 左零空间维数：", r, n-r, r, m-r)
print("行空间与零空间的点积：", null @ row)
print("列空间与左零空间的点积：", column @ left_null)
print("A 作用于零空间：\\n", A @ null.T)
print("A.T 作用于左零空间：", A.T @ left_null)
'''),
 dict(title='找到离目标最近的点', short='正交投影', group='正交与拟合', lead='当目标不在子空间里，投影给出距离它最近的可达点。误差与这个子空间垂直。', formula=r'p=\frac{aa^T}{a^Ta}b,\qquad a^T(b-p)=0', concept='投影矩阵满足 P²=P：已经投影的点，再投影不会移动。正交投影还满足 Pᵀ=P。一般情况下，残差正交给出正规方程。', challenge='把 a 改成 [1.,2.,1.]。观察 p 如何变化，P²=P 是否依然成立？', lectures=[10,11], code='''import numpy as np

a = np.array([1., 1., 1.])
b = np.array([1., 2., 4.])
P = np.outer(a, a) / (a @ a)
p = P @ b
e = b - p
print("投影 p：", p)
print("残差 e：", e)
print("正交验证 aᵀe：", a @ e)
print("P²=P：", np.allclose(P @ P, P))
print("Pᵀ=P：", np.allclose(P.T, P))
assert np.allclose(a @ e, 0.)
'''),
 dict(title='用三个点拟合一条直线', short='最小二乘', group='正交与拟合', lead='数据不必落在同一条线上。选择截距与斜率，让所有竖直误差的平方和最小。', formula=r'\hat x=\arg\min_x\|Ax-b\|_2^2,\qquad A^T(b-A\hat x)=0', concept='第一列全为 1，负责截距；第二列是 t，负责斜率。参数 x 在 R²，三个拟合值 Ax 在 R³。拟合值是观测向量 b 的投影。', challenge='把最后一个观测值从 2 改成 4，再运行。直线怎么移动？残差仍然与两列正交吗？', lectures=[12], code='''import numpy as np
import matplotlib.pyplot as plt

t = np.array([1., 2., 3.])
b = np.array([1., 2., 2.])
A = np.column_stack([np.ones_like(t), t])
x = np.linalg.lstsq(A, b, rcond=None)[0]
p = A @ x
print("截距、斜率：", x)
print("预测值：", p)
print("残差：", b-p)
print("Aᵀe：", A.T @ (b-p))
plt.scatter(t, b, color="#2563eb", label="observations")
plt.plot(t, p, color="#0d9488", label="least squares")
plt.vlines(t, b, p, color="#94a3b8", linestyles="dashed")
plt.xlabel("t")
plt.ylabel("y")
plt.legend()
plt.tight_layout()
plt.show()
'''),
 dict(title='换成一组正交的坐标', short='Gram–Schmidt 与 QR', group='正交与拟合', lead='Q 给列空间一组正交坐标，R 记录原来的列如何在这组坐标里表示。', formula=r'A=QR,\quad Q^TQ=I,\quad R\hat x=Q^Tb', concept='对于 3×2 满列秩矩阵，reduced Q 是 3×2。QᵀQ 是二阶单位阵，QQᵀ 却是三维空间中的投影，不是单位阵。', challenge='打印 Q @ Q.T，对照 T05 的投影矩阵性质；试着解释为什么它的秩只有 2。', lectures=[13], code='''import numpy as np

A = np.array([[1., 1.], [1., 2.], [1., 3.]])
b = np.array([1., 2., 2.])
Q, R = np.linalg.qr(A, mode="reduced")
x = np.linalg.solve(R, Q.T @ b)
print("Q / R 形状：", Q.shape, R.shape)
print("QᵀQ：\\n", Q.T @ Q)
print("QQᵀ：\\n", Q @ Q.T)
print("QR 重建误差：", np.linalg.norm(Q @ R-A))
print("QR 求得参数：", x)
assert np.allclose(x, np.linalg.lstsq(A, b, rcond=None)[0])
'''),
 dict(title='很多个解，选最短的一个', short='最小范数与伪逆', group='正交与拟合', lead='x₁+x₂=2 有无穷多个解。最小范数解是这些点中距离原点最近的一个。', formula=r'A^+b=\arg\min_{Ax=b}\|x\|_2', concept='对有解方程，最小范数解位于行空间；额外的零空间分量只会增加长度。无精确解时，伪逆给出最小范数最小二乘解。', challenge='把 t 改成 0、1、2，比较解的长度，再说明最短解为何没有零空间分量。', lectures=[14], code='''import numpy as np

A = np.array([[1., 1.]])
b = np.array([2.])
x_star = np.linalg.pinv(A) @ b
t = 0.
x = np.array([t, 2.-t])
print("当前解：", x, "长度：", np.linalg.norm(x))
print("最小范数解：", x_star, "长度：", np.linalg.norm(x_star))
print("两解之差处于零空间：", A @ (x-x_star))
print("lstsq 对照：", np.linalg.lstsq(A, b, rcond=None)[0])
'''),
 dict(title='在特殊方向上，矩阵像一个数', short='特征值与对角化', group='谱与分解', lead='特征向量找到矩阵作用后仍留在同一直线上的方向。足够多的独立方向，让矩阵幂变得简单。', formula=r'Av=\lambda v,\qquad A=S\Lambda S^{-1}', concept='n 个线性无关的特征向量才构成特征基。特征值重复不一定有问题，但只有一个独立特征向量的 2×2 Jordan 例子不能对角化。', challenge='把 k 从 5 改到 10。再查看 J-I 的零空间维数，解释为何 J 不能用两个独立特征向量对角化。', lectures=[15,20,21,22], code='''import numpy as np

A = np.array([[2., 1.], [1., 2.]])
values, S = np.linalg.eig(A)
k = 5
Ak = S @ np.diag(values**k) @ np.linalg.inv(S)
print("特征值：", values)
print("特征方程残差：\\n", A @ S - S @ np.diag(values))
print("对角化计算 A 的幂：\\n", Ak)
assert np.allclose(Ak, np.linalg.matrix_power(A, k))
J = np.array([[1., 1.], [0., 1.]])
print("J 的 λ=1 特征空间维数：", 2-np.linalg.matrix_rank(J-np.eye(2)))
'''),
 dict(title='对称性让谱变得清晰', short='对称矩阵与正定性', group='谱与分解', lead='实对称矩阵拥有正交特征基。二次型的正负，可以在这组坐标中直接从特征值读出。', formula=r'x^TAx=\sum_i\lambda_i y_i^2,\qquad y=Q^Tx', concept='所有特征值严格为正是 PD；允许零是 PSD。BᵀB 总是 PSD，因为对应二次型等于 ||Bx||²。一般 Hessian 不一定 PSD。', challenge='把 B 的第二列改成第一列的两倍，观察 B.T @ B 的最小特征值，并解释为何不再正定。', lectures=[23,24], code='''import numpy as np

for diag in ([2., 1.], [2., 0.], [2., -1.]):
    A = np.diag(diag)
    values, Q = np.linalg.eigh(A)
    label = "PD" if np.all(values>0) else "PSD" if np.all(values>=0) else "非 PSD"
    print("特征值：", values, "分类：", label)
B = np.array([[1., 2.], [2., 1.], [1., 1.]])
x = np.array([1., -2.])
print("BᵀB 的特征值：", np.linalg.eigvalsh(B.T @ B))
print("二次型 / 长度平方：", x @ B.T @ B @ x, np.linalg.norm(B @ x)**2)
'''),
 dict(title='任意矩阵都能做 SVD', short='SVD 与四个空间', group='谱与分解', lead='选对输入与输出的正交基，矩阵的作用就变成沿各个方向缩放。', formula=r'A=U\Sigma V^T,\qquad Av_i=\sigma_i u_i', concept='完整 SVD 为输入和输出各提供一组完整正交基。reduced SVD 保留 min(m,n) 个位置，紧致 SVD 只保留 r 个非零奇异值。', challenge='比较 full_matrices=True 和 False 的尺寸。在这个 2×3 例子中，哪个 V 包含完整的二维零空间？', lectures=[24,25,26], code='''import numpy as np

A = np.array([[1., 2., 3.], [2., 4., 6.]])
U, s, Vt = np.linalg.svd(A, full_matrices=False)
Uf, sf, Vtf = np.linalg.svd(A, full_matrices=True)
r = np.linalg.matrix_rank(A)
print("reduced 尺寸：", U.shape, s.shape, Vt.shape)
print("完整 U / Vt 尺寸：", Uf.shape, Vtf.shape)
print("奇异值：", s)
print("重建误差：", np.linalg.norm(U @ np.diag(s) @ Vt-A))
print("完整 V 中的零空间：\\n", Vtf[r:].T)
print("零空间验证：\\n", A @ Vtf[r:].T)
print("伪逆形状：", np.linalg.pinv(A).shape)
'''),
 dict(title='保留最重要的方向', short='低秩近似与 PCA', group='谱与分解', lead='把二维数据投影到变化最大的一条轴，再重建回来。奇异值告诉你损失了多少信息。', formula=r'X_k=U_k\Sigma_k V_k^T,\qquad\|X-X_k\|_F^2=\sum_{i>k}\sigma_i^2', concept='PCA 先按列中心化。右奇异向量是特征空间中的主轴；投影坐标为 XcV。这里不按标准差缩放，以保留原始单位。', challenge='把 k 从 1 改成 2。重建误差与保留方差比例怎么变化？再修改一个数据点重复观察。', lectures=[27,28], code='''import numpy as np
import matplotlib.pyplot as plt

X = np.array([[1., 1.], [2., 2.], [3., 2.], [4., 4.]])
mean = X.mean(axis=0)
Xc = X-mean
U, s, Vt = np.linalg.svd(Xc, full_matrices=False)
k = 1
Z = Xc @ Vt[:k].T
Xk = Z @ Vt[:k] + mean
error = np.linalg.norm(X-Xk)
print("一维坐标：\\n", Z)
print("保留方差比例：", np.sum(s[:k]**2)/np.sum(s**2))
print("相对重建误差：", error/np.linalg.norm(Xc))
assert np.allclose(error**2, np.sum(s[k:]**2))
plt.scatter(*X.T, label="original", color="#2563eb")
plt.scatter(*Xk.T, label="reconstructed", color="#0d9488", marker="x")
for a, b in zip(X, Xk):
    plt.plot([a[0], b[0]], [a[1], b[1]], color="#94a3b8", linestyle="--")
plt.axis("equal")
plt.legend()
plt.tight_layout()
plt.show()
'''),
 dict(title='小误差为什么会变大', short='条件数与数值稳定性', group='数值计算', lead='几乎相关的列让求解变得敏感。答案满足方程，不一定意味着它接近原问题的真实解。', formula=r'\kappa_2(A)=\frac{\sigma_{\max}}{\sigma_{\min}}', concept='条件数描述问题的敏感程度，算法稳定性描述计算过程的误差行为。对固定 A 的右端扰动，条件数界定相对误差的最坏放大。', challenge='把扰动从 [0.,1e-6] 改成 [1e-6,1e-6]。比较两种方向的放大率，解释为何不总达到条件数。', lectures=[], code='''import numpy as np

print("epsilon   cond(A)       相对输入变化    相对解变化    扰动方程残差")
for eps in (1e-2, 1e-4, 1e-6):
    A = np.array([[1., 1.], [1., 1.+eps]])
    b = A @ np.ones(2)
    delta = np.array([0., 1e-6])
    x = np.linalg.solve(A, b)
    xp = np.linalg.solve(A, b+delta)
    input_error = np.linalg.norm(delta)/np.linalg.norm(b)
    solution_error = np.linalg.norm(xp-x)/np.linalg.norm(x)
    residual = np.linalg.norm(A @ xp-(b+delta))
    print(f"{eps:.0e}    {np.linalg.cond(A):.3e}    {input_error:.3e}       {solution_error:.3e}    {residual:.3e}")
print("不同阈值下的数值秩：")
for tol in (1e-8, 1e-5):
    print(tol, np.linalg.matrix_rank(A, tol=tol))
'''),
]
CAPSTONE = dict(title='用一个矩阵串起整条主线',short='综合验收',group='综合验收',lead='先写下判断，再运行代码。从解的存在性出发，经过投影，最终用 SVD 回到四个基本子空间。',formula=r'\hat x=A^+b,\qquad A^T(b-A\hat x)=0',concept='最小范数最小二乘解位于行空间，残差位于左零空间。两者将解方程、正交投影与 SVD 连接起来。',challenge='不看输出，先手算投影、最小范数解与残差。再尝试改为 b=[1.,2.]，说明什么发生了变化。',lectures=[],code='''import numpy as np

A = np.array([[1., 2., 3.], [2., 4., 6.]])
b = np.array([1., 3.])
x = np.linalg.lstsq(A, b, rcond=None)[0]
p = A @ x
e = b-p
U, s, Vt = np.linalg.svd(A, full_matrices=True)
r = np.linalg.matrix_rank(A)
print("秩：", r)
print("最小范数解：", x)
print("投影：", p)
print("残差：", e)
print("左零空间验证：", A.T @ e)
print("解与零空间正交：", Vt[r:] @ x)
assert np.allclose(x, np.linalg.pinv(A) @ b)
''')
