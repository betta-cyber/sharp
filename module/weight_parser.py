# -*- coding: utf-8 -*-

import jieba
import jieba.analyse


def get_rank_text(text):
    # split_text = jieba.cut(text)

    # a = jieba.analyse.extract_tags(text, topK=5, withWeight=True, allowPOS=())
    # print(a)

    keywords_textrank = jieba.analyse.textrank(text, topK=15, withWeight=True)
    # print(keywords_textrank)
    return keywords_textrank


def calculate_weight(text):
    weight = 4
    rank_text = get_rank_text(text)

    keywords = ['违规', '违法', '治理', '警惕', '个人信息', '勒索', '僵尸网络', '网络',
                '安全', 'ctf', '网络安全', '网络安全法', '病毒', '严打', '数据', '数据安全'
                '信息', '泄漏', '法', '施行', '用户', '服务器', '网络攻击', '系统', '互联网',
                '端口', '企业', '中国', '保护', '团队', '设备', '加密', '手机', 'APP',
                '感染', '窃取', '研究', '全球', '政府', '泄露', '隐私', '应用', '发布',
                '威胁', '恶意软件', '恶意', '法律法规']

    for r in rank_text:
        if r[0] in keywords:
            # t = r[1]
            t = 1
        else:
            t = 0
        weight += t

    if weight > 10:
        weight = 10
    return int(weight)


def test():
    text = "2019年1月，中央网信办、工业和信息化部、公安部、市场监管总局四部门联合发布《关于开展APP违法违规收集使用个人信息专项治理的公告》，在全国范围组织开展APP违法违规收集使用个人信息专项治理，并成立APP违法违规收集使用个人信息专项治理工作组。一年来，专项治理工作成效显著，《APP违法违规收集使用个人信息行为认定方法》《个人信息安全规范》等标准规范相继出台完善，用户规模大、与生活关系密切、问题反映集中的千余款APP经深度评估后进行了有效整改，无隐私政策、强制索权、无注销渠道等问题明显改善，APP运营者履行个人信息保护责任义务的能力和水平明显提升，全社会关注和重视个人信息安全的氛围基本形成。《APP违法违规收集使用个人信息专项治理报告（2019）》介绍了治理工作开展情况，包括技术规范制定、举报信息受理、专业机构检测评估、问题督促整改及处置，以及四部门全面推进深化治理等；报告引用多方数据，客观分析了个人信息保护相关突出问题、企业能力、民众意识、社会影响等方面的发展变化趋势，展示了治理工作成效。最后，在总结2019年治理工作经验的基础上，就持续开展治理工作，培育良好移动互联网生态，提出了具体建议。"
    res = calculate_weight(text)
    print(res)


if __name__ == '__main__':
    test()
