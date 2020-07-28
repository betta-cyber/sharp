# -*- coding: utf-8 -*-

import json
import codecs
import os
import pymysql
import logging

logging.basicConfig(filename='debug.log', level=logging.INFO)


cve_tags = ['CVE_Items_cve_data_type' ,'CVE_Items_cve_data_format' ,'CVE_Items_cve_data_version','CVE_Items_cve_CVE_data_meta_ID' ,'CVE_Items_cve_CVE_data_meta_ASSIGNER' ,\
        'CVE_Items_cve_problemtype_problemtype_data_description_lang' ,'CVE_Items_cve_problemtype_problemtype_data_description_value' ,'CVE_Items_cve_problemtype_problemtype_data_description' ,'CVE_Items_cve_references_reference_data' ,'CVE_Items_cve_references_reference_data_url' ,\
        'CVE_Items_cve_references_reference_data_name' ,'CVE_Items_cve_references_reference_data_refsource' ,'CVE_Items_cve_references_reference_data_tags' ,'CVE_Items_cve_description_description_data_lang' ,'CVE_Items_cve_description_description_data_value' ,\
        'CVE_Items_configurations_nodes' ,'CVE_Items_configurations_CVE_data_version' ,'CVE_Items_configurations_nodes_operator' ,'CVE_Items_configurations_nodes_children_operator' ,'CVE_Items_configurations_nodes_children_cpe_match_vulnerable',\
        'CVE_Items_configurations_nodes_children_cpe_match_cpe23Uri' ,\
        'CVE_Items_configurations_nodes_cpe_match_vulnerable' ,'CVE_Items_configurations_nodes_cpe_match_cpe23Uri' ,'CVE_Items_configurations_nodes_cpe_match_versionStartIncluding' ,'CVE_Items_configurations_nodes_cpe_match_versionEndExcluding' ,'CVE_Items_configurations_nodes_cpe_match_versionEndIncluding' ,\
        'CVE_Items_configurations_nodes_cpe_match_versionStartExcluding' ,'CVE_Items_impact_baseMetricV3_cvssV3_version' ,'CVE_Items_impact_baseMetricV3_cvssV3_vectorString' ,'CVE_Items_impact_baseMetricV3_cvssV3_attackVector' ,'CVE_Items_impact_baseMetricV3_cvssV3_attackComplexity' ,\
        'CVE_Items_impact_baseMetricV3_cvssV3_privilegesRequired' ,'CVE_Items_impact_baseMetricV3_cvssV3_userInteraction' ,'CVE_Items_impact_baseMetricV3_cvssV3_scope' ,'CVE_Items_impact_baseMetricV3_cvssV3_confidentialityImpact' ,'CVE_Items_impact_baseMetricV3_cvssV3_integrityImpact' ,\
        'CVE_Items_impact_baseMetricV3_cvssV3_availabilityImpact' ,'CVE_Items_impact_baseMetricV3_cvssV3_baseScore' ,'CVE_Items_impact_baseMetricV3_cvssV3_baseSeverity' ,'CVE_Items_impact_baseMetricV3_exploitabilityScore' ,'CVE_Items_impact_baseMetricV3_impactScore' ,\
        'CVE_Items_impact_baseMetricV2_cvssV2_version' ,'CVE_Items_impact_baseMetricV2_cvssV2_vectorString' ,'CVE_Items_impact_baseMetricV2_cvssV2_accessVector' ,'CVE_Items_impact_baseMetricV2_cvssV2_accessComplexity' ,'CVE_Items_impact_baseMetricV2_cvssV2_authentication' ,\
        'CVE_Items_impact_baseMetricV2_cvssV2_confidentialityImpact' ,'CVE_Items_impact_baseMetricV2_cvssV2_integrityImpact' ,'CVE_Items_impact_baseMetricV2_cvssV2_availabilityImpact' ,'CVE_Items_impact_baseMetricV2_cvssV2_baseScore' ,'CVE_Items_impact_baseMetricV2_severity' ,\
        'CVE_Items_impact_baseMetricV2_exploitabilityScore' ,'CVE_Items_impact_baseMetricV2_impactScore' ,'CVE_Items_impact_baseMetricV2_acInsufInfo' ,'CVE_Items_impact_baseMetricV2_obtainAllPrivilege' ,'CVE_Items_impact_baseMetricV2_obtainUserPrivilege' ,\
        'CVE_Items_impact_baseMetricV2_obtainOtherPrivilege' ,'CVE_Items_impact_baseMetricV2_userInteractionRequired' ,'CVE_Items_publishedDate','CVE_Items_lastModifiedDate' ,'CVE_Items_impact','CVE_EXP_label']


def dict_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                if len(value) == 0:
                    yield pre+[key, '']
                else:
                    for d in dict_generator(value, pre + [key]):
                        yield d
            elif isinstance(value, list):
                if len(value) == 0:
                    yield pre+[key, '']
                else:
                    for v in value:
                        for d in dict_generator(v, pre + [key]):
                            yield d
            elif isinstance(value, tuple):
                if len(value) == 0:
                    yield pre+[key, '']
                else:
                    for v in value:
                        for d in dict_generator(v, pre + [key]):
                            yield d
            else:
                yield pre + [key, value]
    else:
        yield ['.'.join(pre), indict]


def padding(cve_dict, cve_tags):
    """
    填充一条CVE至完整的65个字段
    """
    cve_normal = {}
    for i in cve_tags:
        if i not in cve_dict.keys():
            cve_normal[i] = ''
        else:
            cve_normal[i] = cve_dict[i]
    return cve_normal


def merge_dict(x, y):
    """
    将字典x合并入字典y
    """
    for k, v in x.items():
        if k in y.keys():
            y[k] = str(y[k])+";"+str(v)
        else:
            y[k] = v
    return y


def d2sql(values, table="nvd", action="replace"):
    """
    生成插入数据库预编译语句
    :param d:dict
    :param table:
    :param action:
    :return sql:
    """
    if not values:
        return
    columns = ', '.join(values.keys())
    placeholders = ', '.join(["%s"] * len(values))
    sql = '{} INTO {} ({}) VALUES ({})'.format(action, table, columns, placeholders)

    return sql


def json2tuple_dict(jfile):
    """
    解析json，入库
    """
    with codecs.open(jfile, 'r', encoding='utf-8') as f:
        fjson = json.load(f)

    j = 0
    cve = {}
    all_content = {}
    for i in dict_generator(fjson):
        tp = '.'.join(i[0:-1]).replace('.', '_')
        # 过滤json文件头
        if tp in ['CVE_data_type', 'CVE_data_format', 'CVE_data_version', 'CVE_data_numberOfCVEs', 'CVE_data_timestamp']:
            continue
        value = i[-1]

        # 合并json中的列表数据结构
        cve_now = {}
        cve_now[tp] = str(value)
        cve = merge_dict(cve_now, cve)
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionStartIncluding']
        except Exception:
            pass
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionEndExcluding']
        except Exception:
            pass
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionEndIncluding']
        except Exception:
            pass
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionStartExcluding']
        except Exception:
            pass

        # 一条完整的CVE数据
        if tp == 'CVE_Items_lastModifiedDate':
            cve = padding(cve, cve_tags)
            sql = d2sql(cve)
            if sql:
                j = j+1
                all_content[j] = tuple(cve.values())

            cve = {}
    return sql, all_content


def json2(jfile):
    """
    解析json，入库
    """
    with codecs.open(jfile, 'r', encoding='utf-8') as f:
        fjson = json.load(f)

    j = 0
    cve = {}
    all_content = {}
    for i in dict_generator(fjson):
        tp = '.'.join(i[0:-1]).replace('.', '_')
        # 过滤json文件头
        if tp in ['CVE_data_type', 'CVE_data_format', 'CVE_data_version', 'CVE_data_numberOfCVEs', 'CVE_data_timestamp']:
            continue
        value = i[-1]

        # 合并json中的列表数据结构
        cve_now = {}
        cve_now[tp] = str(value)
        cve = merge_dict(cve_now, cve)
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionStartIncluding']
        except Exception:
            pass
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionEndExcluding']
        except Exception:
            pass
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionEndIncluding']
        except Exception:
            pass
        try:
            del cve['CVE_Items_configurations_nodes_children_cpe_match_versionStartExcluding']
        except Exception:
            pass

        # 一条完整的CVE数据
        if tp == 'CVE_Items_lastModifiedDate':
            cve = padding(cve, cve_tags)
            sql = d2sql(cve)
            if sql:
                j = j+1
                all_content[j] = tuple(cve.values())

            cve = {}
    return sql, all_content



def sql_insert(sql, all_content):
    db = pymysql.connect("10.1.30.29", "root", "root", "eye")
    cursor = db.cursor()

    try:
        logging.info("[+] INSERT NUMBER:%d" % len(all_content))
        cursor.executemany(sql, all_content.values())

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logging.error("[sql]: %s %s" % (sql, str(e)))

    db.close()


def sql_insert_db(sql):
    db = pymysql.connect("10.1.30.29", "root", "root", "eye")
    cursor = db.cursor()

    try:
        cursor.execute(sql)

        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logging.error("[sql]: %s %s" % (sql, str(e)))

    db.close()
