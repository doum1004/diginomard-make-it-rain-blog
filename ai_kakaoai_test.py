from ai_kakaoai import KakaoAI

kakaoAI = KakaoAI()
files = kakaoAI.getKakaoImage('''Test''',
                      'Korean', 3)
files = kakaoAI.getKakaoImage('''In front of Montreal Oldport, solo, kpop idol, k-beauty, (Small, V-shaped face), youthful and elegant. (Big, almond-shaped eyes), very attractive expressive. sophistication. straight nose. elicate and refined''',
                      'Korean', 3)
kakaoAI.getKakaoImageTransform(files[0], 'Korean', 3)